import json

from fastapi import FastAPI, Body, Depends, Request, HTTPException
from app.model import UserLoginSchema
from app.auth.auth_handler import signJWT
from app.auth.auth_bearer import JWTBearer
from datetime import datetime, timedelta 


##################### ACCESS JSON #########################
with open("user.json", "r") as read_file: 
    usr = json.load(read_file)

with open("infobuku.json", "r") as read_file: 
    info = json.load(read_file)

with open("peminjaman.json", "r") as read_file:
    pinjam = json.load(read_file)

app = FastAPI()

@app.get("/")
def root():
    return {"Welcome! This is a BOOK BORROWING-API by Kelompok 06-Kelas K1. Hope you enjoy it."}

##################### LOGIN USER #########################
def check_user(info: UserLoginSchema):
    for user in usr['user']:
        if user["username"] == info.username and user["password"] == info.password:
            return True
    return False

def check_user(pinjam: UserLoginSchema):
    for user in usr['user']:
        if user["username"] == pinjam.username and user["password"] == pinjam.password:
            return True
    return False

@app.post("/user/login", tags=["User"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.username)
    return {
        "error": "Wrong username or password!"
    }


##################### INFO BUKU #########################
#read all item
@app.get('/info', dependencies=[Depends(JWTBearer())], tags=["Informasi Buku"])
async def read_all_book():
    return info

#read an item
@app.get('/info/judulbuku', dependencies=[Depends(JWTBearer())], tags=["Informasi Buku"]) 
async def read_info(judulbuku: str) -> dict: 
    for buku_item in info['infobuku']:
        if buku_item['judulbuku'] == judulbuku:
            return buku_item
    raise HTTPException(
        status_code=404, detail=f'Buku tidak ditemukan'
        )


##################### REKOMENDASI BUKU #########################
#rekomendasi by kategori
@app.get('/rekomendasi/kategori', dependencies=[Depends(JWTBearer())], tags=["Rekomendasi Buku"])
async def read_rekom(kategori: str) -> dict:
    for info_buku in info['infobuku']:
        if info_buku['kategori'] == kategori:
            return info_buku
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

#rekomendasi by jurusan
@app.get('/rekomendasi/jurusan', dependencies=[Depends(JWTBearer())], tags=["Rekomendasi Buku"])
async def read_rekom(jurusan: str) -> dict:
    for info_buku in info['infobuku']:
        if info_buku['rekomendasi'] == jurusan:
            return info_buku
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

##################### PEMINJAMAN BUKU #########################
@app.patch('/user/peminjaman/', dependencies=[Depends(JWTBearer())], tags=["Peminjaman Buku"])
async def peminjaman(namapeminjam : str, judulbuku : str) :
    for user in usr['user']:
        if user['nama-mhs'] == namapeminjam :
            for info_buku in info['infobuku']:
                if info_buku['judulbuku'] == judulbuku:
                    if info_buku['stok'] == 0 :
                        return ({'Message' : 'Buku yang ingin dipinjam sedang kosong.'})
                    else :
                        new_data = {'namapeminjam': namapeminjam, 'judul': judulbuku, 'tglpinjam': str(datetime.date(datetime.now())), 'tglkembali': str(datetime.date(datetime.now() + timedelta(days=7)))}
                        pinjam['peminjaman'].append(new_data)

                        read_file.close()
                        with open("peminjaman.json", "w") as write_file:
                            json.dump(pinjam, write_file, indent = 4)
                        write_file.close()

                        info_buku['stok'] = info_buku['stok'] - 1
                        with open("infobuku.json", "w") as write_file:
                            json.dump(info, write_file, indent = 4)
                        write_file.close()
                        return ({'Message' : 'Peminjaman buku berhasil dilakukan!'})
                        
            raise HTTPException(
                status_code = 404, detail =f'Buku tidak ditemukan'
                )
    raise HTTPException(
        status_code = 404, detail =f'Nama peminjam tidak valid'
        )

#read item peminjaman
@app.get('/user/detailpinjam', dependencies=[Depends(JWTBearer())], tags=["Peminjaman Buku"]) 
async def read_pinjam(namapeminjam : str) -> dict: 
    for pinjam_item in pinjam['peminjaman']:
        if pinjam_item['namapeminjam'] == namapeminjam:
            return pinjam_item
    raise HTTPException(
        status_code = 404, detail =f'Nama peminjam tidak valid'
        )