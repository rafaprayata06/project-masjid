
from flask import request, redirect, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from database.db import db
from models.transaksi_model import Transaksi
from models.kategori_model import Kategori
from datetime import datetime
import os
from sqlalchemy import func
from flask import send_file
from openpyxl import Workbook
from io import BytesIO


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def validate_transaksi_form(
    kategori_id,
    jumlah,
    created_at,
    keterangan
):
    errors = {}

    if not kategori_id:
        errors["kategori"] = "Kategori wajib dipilih"

    if not jumlah:
        errors["jumlah"] = "Nominal wajib diisi"

    if not created_at:
        errors["created_at"] = "Tanggal transaksi wajib diisi"

    if not keterangan or not keterangan.strip():
        errors["keterangan"] = "Keterangan wajib diisi"

    return errors

def handle_bukti_upload(file,old_bukti=None):

    if not file or file.filename == "":
        return old_bukti

    if not allowed_file(file.filename):
        raise ValueError(
            "Format gambar harus JPG, JPEG, PNG, atau WEBP"
        )

    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    if file_length > MAX_FILE_SIZE:
        raise ValueError(
            "Ukuran gambar maksimal 2MB"
        )

    # HAPUS FILE LAMA JIKA ADA
    if old_bukti:

        old_path = os.path.join(
            "static",
            old_bukti
        )

        if os.path.exists(old_path):
            os.remove(old_path)

    filename = (
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}_"
        f"{secure_filename(file.filename)}"
    )

    upload_folder = os.path.join(
        "static",
        "uploads",
        "transaksi"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_folder,
        filename
    )

    file.save(file_path)

    return f"uploads/transaksi/{filename}"
def admin_keuangan_store():

    try:

        kategori_id = request.form.get("kategori_id")
        jumlah = request.form.get("jumlah")
        created_at = request.form.get("created_at")
        keterangan = request.form.get("keterangan")

        errors = validate_transaksi_form(
            kategori_id,
            jumlah,
            created_at,
            keterangan
        )

        if errors:

            for error in errors.values():
                flash(error, "error")

            return redirect("/admin-keuangan/finance")

        kategori = Kategori.query.get(kategori_id)

        if not kategori:
            flash("Kategori tidak ditemukan", "error")
            return redirect("/admin-keuangan/finance")

        file = request.files.get("bukti_transaksi")

        bukti_transaksi = None

        # wajib upload jika kategori pengeluaran
        if kategori.jenis == "PENGELUARAN":

            if not file or file.filename == "":
                flash(
                    "Bukti transaksi wajib diupload untuk pengeluaran",
                    "error"
                )
                return redirect("/admin-keuangan/finance")

            bukti_transaksi = handle_bukti_upload(file)

        transaksi = Transaksi(

            user_nim=current_user.nim,

            kategori_id=int(kategori_id),

            jumlah=float(jumlah),

            keterangan=keterangan,

            bukti_transaksi=bukti_transaksi,

            created_at=datetime.strptime(
                created_at,
                "%Y-%m-%dT%H:%M"
            )

        )

        db.session.add(transaksi)
        db.session.commit()

        flash(
            "Transaksi berhasil ditambahkan!",
            "success"
        )

    except ValueError as e:

        flash(str(e), "error")

    except Exception as e:

        db.session.rollback()

        flash(
            f"Gagal menambahkan transaksi: {str(e)}",
            "error"
        )

    return redirect("/admin-keuangan/finance")

def export_keuangan():

    jenis = request.args.get("jenis")
    kategori_id = request.args.get("kategori_id")
    bulan = request.args.get("bulan")
    tanggal_awal = request.args.get("tanggal_awal")
    tanggal_akhir = request.args.get("tanggal_akhir")

    query = (
        Transaksi.query
        .join(Kategori)
    )

    # FILTER JENIS
    if jenis:
        query = query.filter(
            Kategori.jenis == jenis
        )

    # FILTER KATEGORI
    if kategori_id:
        query = query.filter(
            Transaksi.kategori_id == int(kategori_id)
        )

    # FILTER BULAN
    if bulan:
        query = query.filter(
            db.extract(
                "month",
                Transaksi.created_at
            ) == int(bulan)
        )

    # FILTER TANGGAL AWAL
    if tanggal_awal:
        query = query.filter(
            Transaksi.created_at >= datetime.strptime(
                tanggal_awal,
                "%Y-%m-%d"
            )
        )

    # FILTER TANGGAL AKHIR
    if tanggal_akhir:
        query = query.filter(
            Transaksi.created_at <= datetime.strptime(
                tanggal_akhir,
                "%Y-%m-%d"
            )
        )

    transaksi_list = (
        query
        .order_by(
            Transaksi.created_at.desc()
        )
        .all()
    )

    workbook = Workbook()
    worksheet = workbook.active

    worksheet.title = "Laporan Keuangan"

    worksheet.append([
        "Tanggal",
        "Kategori",
        "Jenis",
        "Nominal",
        "Keterangan"
    ])

    for transaksi in transaksi_list:

        worksheet.append([
            transaksi.created_at.strftime("%d-%m-%Y"),
            transaksi.kategori.nama,
            transaksi.kategori.jenis,
            float(transaksi.jumlah),
            transaksi.keterangan
        ])

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="laporan_keuangan.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def edit_transaksi(id):

    try:

        transaksi = (
            Transaksi.query
            .get_or_404(id)
        )

        kategori_id = request.form.get(
            "kategori_id"
        )

        jumlah = request.form.get(
            "jumlah"
        )

        created_at = request.form.get(
            "created_at"
        )

        keterangan = request.form.get(
            "keterangan"
        )

        errors = validate_transaksi_form(
            kategori_id,
            jumlah,
            created_at,
            keterangan
        )

        if errors:

            for error in errors.values():
                flash(error, "error")

            return redirect(
                "/admin-keuangan/finance"
            )

        kategori = Kategori.query.get(
            kategori_id
        )

        if not kategori:

            flash(
                "Kategori tidak ditemukan",
                "error"
            )

            return redirect(
                "/admin-keuangan/finance"
            )

        file = request.files.get(
            "bukti_transaksi"
        )

        # WAJIB BUKTI JIKA PENGELUARAN
        if kategori.jenis == "PENGELUARAN":

            if (
                not transaksi.bukti_transaksi
                and
                (
                    not file
                    or
                    file.filename == ""
                )
            ):

                flash(
                    "Bukti transaksi wajib diupload untuk pengeluaran",
                    "error"
                )

                return redirect(
                    "/admin-keuangan/finance"
                )

        transaksi.kategori_id = int(
            kategori_id
        )

        transaksi.jumlah = float(
            jumlah
        )

        transaksi.keterangan = (
            keterangan
        )

        transaksi.created_at = (
            datetime.strptime(
                created_at,
                "%Y-%m-%dT%H:%M"
            )
        )

        transaksi.bukti_transaksi = (
            handle_bukti_upload(
                file,
                transaksi.bukti_transaksi
            )
        )

        db.session.commit()

        flash(
            "Transaksi berhasil diupdate!",
            "success"
        )

    except ValueError as e:

        flash(
            str(e),
            "error"
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f"Gagal update transaksi: {str(e)}",
            "error"
        )

    return redirect(
        "/admin-keuangan/finance"
    )