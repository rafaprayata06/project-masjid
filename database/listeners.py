# database/listeners.py
from flask_login import current_user
from flask import has_request_context
from database.db import db
from models.activity_log_model import ActivityLog
from sqlalchemy import event

def capture_log(session, flush_context, instances):
    """
    Fungsi internal untuk mendeteksi perubahan data saat session.flush() atau session.commit()
    """
    # Pastikan ini berjalan di dalam request HTTP (bukan CLI/seeding script)
    if not has_request_context():
        return

    # Saring hanya jika user sudah login dan rolenya adalah AH atau AK
    if not current_user.is_authenticated or current_user.role not in ['AH', 'AK']:
        return

    # 1. Deteksi DATA BARU (CREATE)
    for obj in session.new:
        if isinstance(obj, ActivityLog): 
            continue # Jangan melog tabel log itu sendiri (bisa infinity loop)
        
        # Ambil primary key setelah data siap dimasukkan
        target_id = getattr(obj, 'id', getattr(obj, 'nim', None))
        
        log = ActivityLog(
            user_nim=current_user.nim,
            action="CREATE",
            target_table=obj.__tablename__,
            target_id=str(target_id) if target_id else "Baru",
            deskripsi=f"Menambahkan data baru ke tabel {obj.__tablename__}"
        )
        session.add(log)

    # 2. Deteksi PERUBAHAN DATA (UPDATE)
    for obj in session.dirty:
        if isinstance(obj, ActivityLog): 
            continue
        
        target_id = getattr(obj, 'id', getattr(obj, 'nim', None))
        
        # Opsional: Mendeteksi kolom apa saja yang berubah
        state = db.inspect(obj)
        changes = []
        for attr in state.attrs:
            history = attr.history
            if history.has_changes():
                changes.append(f"Kolom '{attr.key}' diubah")

        deskripsi_log = f"Mengubah data pada tabel {obj.__tablename__}."
        if changes:
            deskripsi_log += " Detail: " + ", ".join(changes)

        log = ActivityLog(
            user_nim=current_user.nim,
            action="UPDATE",
            target_table=obj.__tablename__,
            target_id=str(target_id) if target_id else None,
            deskripsi=deskripsi_log
        )
        session.add(log)

    # 3. Deteksi PENGHAPUSAN DATA (DELETE)
    for obj in session.deleted:
        if isinstance(obj, ActivityLog): 
            continue
        
        target_id = getattr(obj, 'id', getattr(obj, 'nim', None))
        
        log = ActivityLog(
            user_nim=current_user.nim,
            action="DELETE",
            target_table=obj.__tablename__,
            target_id=str(target_id) if target_id else None,
            deskripsi=f"Menghapus data dari tabel {obj.__tablename__}"
        )
        session.add(log)

# Daftarkan fungsi pemantau di atas ke event global SQLAlchemy sebelum database melakukan penulisan (flush)
event.listen(db.session, 'before_flush', capture_log)