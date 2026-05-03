from flask import Blueprint, render_template
from models.berita_model import Berita
import requests

public = Blueprint('public', __name__)

def get_jadwal():
    url = "https://api.aladhan.com/v1/timingsByCity?city=Jakarta&country=Indonesia"
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
    berita_data = Berita.query.order_by(Berita.created_at.desc()).all()
    return render_template('public/home.html',
        jadwal=jadwal,
        tanggal=tanggal,
        berita=berita_data
    )

@public.route('/jadwal')
def jadwal():
    jadwal, tanggal = get_jadwal()
    return render_template('public/jadwal.html',
        jadwal=jadwal,
        tanggal=tanggal
    )

@public.route('/berita')
def berita():
    data = Berita.query.order_by(Berita.created_at.desc()).all()
    return render_template('public/berita.html', berita=data)

@public.route('/berita/<int:id>')
def berita_detail(id):
    b = Berita.query.get_or_404(id)
    return render_template('public/detail_berita.html', berita=b)

@public.route('/galeri')
def galeri():
    return render_template('public/galeri.html')

@public.route('/tentang')
def tentang():
    return render_template('public/tentang.html')