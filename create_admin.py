from getpass import getpass
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models
from app.auth.utils import hash_password

def create_admin():
    db: Session = SessionLocal()

    # Cek apakah sudah ada admin
    existing_admin = db.query(models.User).filter(models.User.role == models.RoleEnum.admin).first()
    if existing_admin:
        print("❌ Admin sudah ada. Tidak bisa membuat admin kedua lewat CLI.")
        return

    print("👤 Membuat akun admin pertama:")
    name = input("Nama lengkap: ")
    username = input("Username: ")
    email = input("Email: ")
    address = input("Alamat: ")
    phone = input("No. HP: ")

    while True:
        password = getpass("Password: ")
        confirm_password = getpass("Konfirmasi Password: ")
        if password == confirm_password:
            break
        print("❗Password tidak cocok. Ulangi.")

    # Buat admin user
    admin_user = models.User(
        name=name,
        username=username,
        email=email,
        password=hash_password(password),
        address=address,
        phone=phone,
        role=models.RoleEnum.admin
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    print(f"✅ Admin '{admin_user.username}' berhasil dibuat.")

if __name__ == "__main__":
    create_admin()
