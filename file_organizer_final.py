import os
import shutil
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.attributes('-topmost', True)  # بيخلي النافذة تطلع فوق كل حاجة
folder_path = filedialog.askdirectory(title="Choose a folder")
root.destroy()

# سؤال الإذن بلون أصفر
print("\033[93mThis program will access and move files on your device. Allow? (y/n): \033[0m", end="")
allow = input().lower()
if allow != "y":
    print("Cancelled.")
    exit()

if not os.path.exists(folder_path):
    print(f"Error: The folder '{folder_path}' does not exist!")
else:
    # خيارات مخصصة
    print("\nChoose file types to organize:")
    organize_images = input("Organize images? (y/no): ").lower() == "y"
    organize_pdfs   = input("Organize PDFs? (y/no): ").lower() == "y"
    organize_videos = input("Organize videos? (y/no): ").lower() == "y"
    organize_others = input("Organize others? (y/no): ").lower() == "y"

    # سؤال التأكيد
    confirm = input(f"\nOrganize files in: {folder_path}\nContinue? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled.")
        exit()

    counts     = {"Images": 0, "PDFs": 0, "Videos": 0, "Others": 0}
    total_size = {"Images": 0, "PDFs": 0, "Videos": 0, "Others": 0}
    failed     = []

    for current_folder, dirs, files in os.walk(folder_path):
        # تجاهل المجلدات اللي احنا بنعملها
        dirs[:] = [d for d in dirs if d not in ["Images", "PDFs", "Videos", "Others"]]

        for file in files:
            file_path = os.path.join(current_folder, file)

            if os.path.isfile(file_path):
                # تصنيف
                if file.lower().endswith((".jpg", ".png", ".gif", ".jpeg", ".bmp", ".webp")):
                    folder_name     = "Images"
                    should_organize = organize_images
                elif file.lower().endswith(".pdf"):
                    folder_name     = "PDFs"
                    should_organize = organize_pdfs
                elif file.lower().endswith((".mp4", ".avi", ".mkv", ".mov", ".wmv")):
                    folder_name     = "Videos"
                    should_organize = organize_videos
                else:
                    folder_name     = "Others"
                    should_organize = organize_others

                if not should_organize:
                    continue

                # احسب الحجم قبل النقل
                file_size = os.path.getsize(file_path)

                # المجلد الهدف في نفس مكان الملف
                target_folder = os.path.join(current_folder, folder_name)
                if not os.path.exists(target_folder):
                    os.mkdir(target_folder)

                target_file = os.path.join(target_folder, file)

                # حماية من الملفات المكررة
                if os.path.exists(target_file):
                    choice = input(f"'{file}' already exists! (rename/skip/replace): ").lower()
                    if choice == "skip":
                        failed.append(file)
                        continue
                    elif choice == "rename":
                        base, ext = os.path.splitext(file)
                        counter = 1
                        while os.path.exists(target_file):
                            target_file = os.path.join(target_folder, f"{base} ({counter}){ext}")
                            counter += 1
                    elif choice == "replace":
                        os.remove(target_file)

                try:
                    shutil.move(file_path, target_file)
                    counts[folder_name]     += 1
                    total_size[folder_name] += file_size
                    print(f"  Moved: {file} → {folder_name}/")
                except Exception as e:
                    failed.append(f"{file} → {e}")

    # حذف المجلدات الفارغة
    for current_folder, dirs, files in os.walk(folder_path, topdown=False):
        for folder_name in ["Images", "PDFs", "Videos", "Others"]:
            folder = os.path.join(current_folder, folder_name)
            if os.path.exists(folder) and not os.listdir(folder):
                os.rmdir(folder)

    # الملخص
    print("\n--- Done! ---")
    for name in ["Images", "PDFs", "Videos", "Others"]:
        size_mb = round(total_size[name] / (1024 * 1024), 2)
        print(f"{name:<10}: {counts[name]} files  ({size_mb} MB)")
    print(f"{'Total':<10}: {sum(counts.values())} files")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  - {f}")
            