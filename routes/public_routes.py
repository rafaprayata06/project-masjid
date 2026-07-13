import requests  
from flask import Blueprint, render_template, request
from models.berita_model import Berita
from models.ustadz_model import Ustadz
from models.jadwal_khutbah_model import JadwalKhutbah
from models.transaksi_model import Transaksi 
from models.kategori_model import Kategori 
from database.db import db
from sqlalchemy import or_, extract, func
from datetime import date, datetime

public = Blueprint('public', __name__)

def get_jadwal():
    url = "https://api.aladhan.com/v1/timingsByCity?city=Jakarta&country=Indonesia&method=20"
    res = requests.get(url)
    data = res.json()
    all_timings = data['data']['timings']
    list_jadwal = {
        'Subuh': all_timings['Fajr'],
        'Dzuhur': all_timings['Dhuhr'],
        'Ashar': all_timings['Asr'],
        'Maghrib': all_timings['Maghrib'],
        'Isya': all_timings['Isha']
    }
    hijri = data['data']['date']['hijri']
    tanggal = f"{data['data']['date']['readable']} | {hijri['day']} {hijri['month']['en']} {hijri['year']} H"
    return list_jadwal, tanggal

@public.route('/')
def home():
    jadwal, tanggal = get_jadwal()
    berita_data = Berita.query.filter(Berita.status == 'publish').order_by(Berita.created_at.desc()).limit(3).all()
    
    hari_ini = date.today()
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    bulan_aktif = nama_bulan[hari_ini.month - 1]

    jadwal_khutbah_data = JadwalKhutbah.query.filter(
        extract('month', JadwalKhutbah.tanggal) == hari_ini.month,
        extract('year', JadwalKhutbah.tanggal) == hari_ini.year
    ).order_by(JadwalKhutbah.tanggal.asc()).all()

    total_masuk = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PEMASUKAN').scalar() or 0
    total_keluar = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PENGELUARAN').scalar() or 0
    saldo_aktif = total_masuk - total_keluar

    transaksi_terbaru = Transaksi.query.order_by(Transaksi.created_at.desc()).limit(5).all()

    # Ambil 6 dokumentasi foto berita terbaru untuk halaman Home
    galeri_home = Berita.query.filter(
        Berita.status == 'publish', 
        Berita.thumbnail != None, 
        Berita.thumbnail != ''
    ).order_by(Berita.created_at.desc()).limit(6).all()

    return render_template('public/home.html',
        jadwal=jadwal,
        tanggal=tanggal,
        berita=berita_data,
        jadwal_khutbah=jadwal_khutbah_data,
        hari_ini=hari_ini,
        bulan_aktif=bulan_aktif,
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        saldo_aktif=saldo_aktif,
        transaksi_terbaru=transaksi_terbaru,
        galeri=galeri_home
    )

@public.route('/berita')
def berita():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    kategori_filter = request.args.get('kategori', '').strip()
    sort_by = request.args.get('sort', 'terbaru').strip()

    query = Berita.query.filter(Berita.status == 'publish')

    if search_query:
        query = query.filter(
            or_(
                Berita.judul.ilike(f"%{search_query}%"),
                Berita.isi.ilike(f"%{search_query}%")
            )
        )

    if kategori_filter:
        query = query.filter(Berita.kategori.ilike(f"%{kategori_filter}%"))

    if sort_by == 'populer':
        query = query.order_by(Berita.views.desc(), Berita.created_at.desc())
    else:
        query = query.order_by(Berita.created_at.desc())

    pagination = query.paginate(page=page, per_page=6, error_out=False)
    data_berita = pagination.items

    return render_template(
        'public/berita.html', 
        berita=data_berita, 
        pagination=pagination,
        search_query=search_query,
        kategori_filter=kategori_filter,
        sort_by=sort_by
    )

@public.route('/berita/<int:id>')
def berita_detail(id):
    b = Berita.query.get_or_404(id)
    return render_template('public/detail_berita.html', berita=b)

@public.route('/donasi')
def donasi():
    return render_template('public/donasi.html')

@public.route('/galeri')
def galeri():
    page = request.args.get('page', 1, type=int)
    kategori_filter = request.args.get('kategori', '').strip()

    # Base query untuk mengambil berita yang sudah publish dan memiliki thumbnail
    query = Berita.query.filter(Berita.status == 'publish', Berita.thumbnail != None, Berita.thumbnail != '')

    # Menggunakan konsep filter yang sama dengan rute berita (ilike)
    if kategori_filter:
        query = query.filter(Berita.kategori.ilike(f"%{kategori_filter}%"))

    # Urutkan berdasarkan yang terbaru
    query = query.order_by(Berita.created_at.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    data_galeri = pagination.items

    return render_template('public/galeri.html', 
        galeri=data_galeri, 
        pagination=pagination, 
        kategori_filter=kategori_filter
    )

@public.route('/tentang')
def tentang():
    return render_template('public/tentang.html')

@public.route('/keuangan')
def halaman_keuangan():
    search_query = request.args.get('q', '')
    jenis_filter = request.args.get('jenis', 'Semua') 
    kategori_id = request.args.get('kategori', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Transaksi.query.join(Kategori)

    if search_query:
        query = query.filter(Transaksi.keterangan.ilike(f"%{search_query}%"))
    
    if jenis_filter != 'Semua':
        query = query.filter(Kategori.jenis == jenis_filter)
        
    if kategori_id:
        query = query.filter(Transaksi.kategori_id == kategori_id)
        
    if start_date:
        query = query.filter(Transaksi.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaksi.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))

    query = query.order_by(Transaksi.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data_transaksi = pagination.items

    total_masuk_filter = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PEMASUKAN')
    total_keluar_filter = db.session.query(func.sum(Transaksi.jumlah)).join(Kategori).filter(Kategori.jenis == 'PENGELUARAN')

    if search_query:
        total_masuk_filter = total_masuk_filter.filter(Transaksi.keterangan.ilike(f"%{search_query}%"))
        total_keluar_filter = total_keluar_filter.filter(Transaksi.keterangan.ilike(f"%{search_query}%"))
    if jenis_filter != 'Semua':
        total_masuk_filter = total_masuk_filter.filter(Kategori.jenis == jenis_filter)
        total_keluar_filter = total_keluar_filter.filter(Kategori.jenis == jenis_filter)
    if kategori_id:
        total_masuk_filter = total_masuk_filter.filter(Transaksi.kategori_id == kategori_id)
        total_keluar_filter = total_keluar_filter.filter(Transaksi.kategori_id == kategori_id)
    if start_date:
        total_masuk_filter = total_masuk_filter.filter(Transaksi.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
        total_keluar_filter = total_keluar_filter.filter(Transaksi.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        total_masuk_filter = total_masuk_filter.filter(Transaksi.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
        total_keluar_filter = total_keluar_filter.filter(Transaksi.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))

    total_masuk_hasil = total_masuk_filter.scalar() or 0
    total_keluar_hasil = total_keluar_filter.scalar() or 0
    total_data_hasil = pagination.total

    list_kategori = Kategori.query.all()

    return render_template('public/keuangan.html',
        transaksi=data_transaksi,
        pagination=pagination,
        total_masuk=total_masuk_hasil,
        total_keluar=total_keluar_hasil,
        total_data=total_data_hasil,
        list_kategori=list_kategori,
        q=search_query,
        jenis=jenis_filter,
        kat_id=kategori_id,
        start_date=start_date,
        end_date=end_date
    )