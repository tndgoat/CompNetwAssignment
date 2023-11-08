from tkinter import *
import tkinter as tk
import sys
import os
from tkinter import messagebox
from tkinter import simpledialog
from database import database
from model.Peer import Peer
from model.Peer import Peer_account
from model.File import File
from model import peer_repository
from model import file_repository
import uuid
import threading
import socket
from utils import shell_colors as shell
import tqdm
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from PyQt5.Qt import QApplication as QApp
from tkinter import filedialog, messagebox
from service import handler
from tkinter import ttk
import multiprocessing

db_file = 'directory.db'


# Xu ly dang ky cho Client va luu thong tin Client vao database
def register_user(root, username: str, password: str, password_rep: str):
    if username and password and password_rep:
        if(password_rep != password):
            messagebox.showerror("Lỗi", "Mật khẩu không khớp!")
        else:
          # ket noi voi database de kiem tra xem tinh xac thuc cua tai khoan
          try:
            conn = database.get_connection(db_file)
            conn.row_factory = database.sqlite3.Row
          except database.Error as e:
            print(f'Error: {e}')
          # Đây là nơi để xử lý việc lưu thông tin người dùng vào cơ sở dữ liệu hoặc tập tin
          # Trong ví dụ này, chúng ta chỉ hiển thị một thông báo
          peer_account = peer_repository.find_account(conn, username=username)
          if peer_account is not None:
            messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại, vui lòng chọn tên khác.")
          else:
            session_id = str(uuid.uuid4().hex[:16].upper())
            peer = peer_repository.find(conn, session_id)
            while peer is not None:
              session_id = str(uuid.uuid4().hex[:16].upper())
              peer = peer_repository.find(conn, session_id)
            peer_account = Peer_account(session_id=session_id, username=username, password=password)
            peer_account.insert(conn=conn)
            conn.commit()
            message = f"Đăng ký tài khoản thành công!\nTên tài khoản: {username}\nMật khẩu: {password}"
            messagebox.showinfo("Đăng ký thành công", message)
            root.destroy()
            show_account_info(session_id=session_id)
    else:
        messagebox.showerror("Lỗi", "Vui lòng điền cả tên tài khoản và mật khẩu.")


# Tao cua so dang ki cho Client
def register(root):
  root.destroy()
  # tao cua so chinh dang ki tai khoan
  root = tk.Tk()
  root.title("Đăng ký tài khoản")

  # Tao cac o dien thong tin
  username_label = tk.Label(root, text="Tên tài khoản:")
  username_label.pack()
  username_entry = tk.Entry(root)
  username_entry.pack()

  password_label = tk.Label(root, text="Mật khẩu:")
  password_label.pack()
  password_entry = tk.Entry(root, show="*")  # Mat khau Client nhap vao se bi an
  password_entry.pack()

  password_rep_label = tk.Label(root, text="Xác nhận mật khẩu:")
  password_rep_label.pack()
  password_rep_entry = tk.Entry(root, show="*")  # Mat khau Client nhap vao se bi an
  password_rep_entry.pack()

  # Tao nut dang ki
  register_button = tk.Button(root, text="Đăng ký", command=lambda: register_user(root, username_entry.get(), password_entry.get(), password_rep_entry.get()))
  register_button.pack()

  root.mainloop()


# cap nhat thong tin Client dang nhap he thong vao database
def save_peer(root, session_id, ip, your_name, port):
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row

  except database.Error as e:
    print(f'Error: {e}')

  peer = Peer(session_id=session_id, ip = ip, your_name = your_name, port = port, state_on_off=False)
  peer.insert(conn=conn)
  conn.commit()

  root.destroy()

  login()


# Dong cua so dang ki -> nhap thong tin co ban
def show_account_info(session_id: str):
    account_info_window = tk.Tk()
    account_info_window.title("Thông tin tài khoản")
    
    username_label = tk.Label(account_info_window, text="Tên của bạn:")
    username_label.pack()
    username_entry = tk.Entry(account_info_window)
    username_entry.pack()

    port_label = tk.Label(account_info_window, text="Source port:")
    port_label.pack()
    port_entry = tk.Entry(account_info_window)
    port_entry.pack()
    
    # tao nut luu thong tin dang ki
    close_button = tk.Button(account_info_window, text="Save", command=lambda: save_peer(account_info_window, session_id=session_id, ip=socket.gethostbyname(socket.gethostname()), your_name = username_entry.get(), port= port_entry.get()))
    close_button.pack()

    account_info_window.mainloop()


# Client main view
def main_view(session_id:str):
  def add_file_to_list():
    file_path = filedialog.askopenfilename()  # Hiển thị hộp thoại mở tệp và lấy đường dẫn tệp đã chọn
    if file_path:
        new_file_name = simpledialog.askstring("Nhập fname", "Nhập tên fname cho file này:")
        if new_file_name:
            file_name = file_path.split('/')[-1]
            modified_file_name = file_name + "%" +new_file_name  # Tạo tên mới theo format mong muốn
            
            # Display the modified file name in the list
            treeview.insert("", "end", values=(file_name, modified_file_name))

            handler.serve(f"ADDF_{modified_file_name.split('/')[-1]}_{session_id}".encode('utf-8'), socket.gethostbyname(socket.gethostname()))
  
  def check(treeview, conn, session_id):
    file_list = peer_repository.get_files_by_peer(conn=conn, session_id=session_id)
    for item in treeview.get_children():
      treeview.delete(item)
    for file in file_list:
      treeview.insert("", "end", values=(file['file_name'], file['file_md5']))
    root.after(100, lambda: check(treeview=treeview, conn=conn, session_id=session_id))
  
  def find_source_files(treeview, message):
    list_source = handler.find(message)
    for item in treeview.get_children():
      treeview.delete(item)
    
    treeview.grid(row=3, column= 0, padx= 0, pady= 0)
    treeview.heading("Column 1", text="fname")
    treeview.heading("Column 2", text="File ID")
    treeview.heading("Column 3", text="Name")
    treeview.heading("Column 4", text="IP Address")
    treeview.heading("Column 5", text="Port")
    treeview.column("Column 1", anchor="center")
    treeview.column("Column 2", anchor="center")
    treeview.column("Column 3", anchor="center")
    treeview.column("Column 4", anchor="center")
    treeview.column("Column 5", anchor="center")
    
    if list_source:
      for source in list_source:
        if source['state_on_off']:
          treeview.insert("", "end",
              values=(source['file_name'].split('%')[-1],
                      source['file_md5'],
                      source['your_name'],
                      source['ip'],
                      source['port']))

  def download_from_source(event):
    selected_item = treeview_x.focus()
    values = treeview_x.item(selected_item, 'values')
    if values:
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
      HOST_download = values[3]
      PORT_download = int(values[4])
      client_socket.connect((HOST_download, PORT_download))
      client_socket.send(f"Please send me {values[0]}".encode('utf-8'))

      try:
        conn = database.get_connection(db_file)
        conn.row_factory = database.sqlite3.Row
      except database.Error as e:
        print(f'Error: {e}')
      
      print(session_id)
      peer = peer_repository.find(conn, session_id)
      message = f"Tôi là \"{peer.your_name}\". Bạn có thể gửi cho tôi file \"{values[0]}\" được không?"
      decoded_message = message.encode('utf-8').decode('utf-8')
      messagebox.showinfo("Require", decoded_message)
      print("\n")
      file_name = client_socket.recv(1024).decode()
      print(f"File name: {file_name}")
      file_size = client_socket.recv(1024).decode()
      print(f"File size: {file_size}")

      file = open(file_name, "wb")
      file_bytes = b""
      done = False
      pbar  = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size)) 

      while not done:
        data = client_socket.recv(1024)
        if file_bytes[-5:] == b"<END>":
          done = True
        else:
          file_bytes += data
        pbar.update(1024)
      pbar.close()
      success_label = tk.Label(root, text="Successful download!", font=("Roboto", 24))
      success_label.grid(row=4, column=0, padx=10, pady=10)
      file.write(file_bytes)
      file.close()
      client_socket.close()
      root.after(1000,lambda: success_label.destroy())

  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  
  file_list = peer_repository.get_files_by_peer(conn=conn, session_id=session_id)
  
  # Tạo cửa sổ chính
  root = tk.Tk()
  root.title("Main user view")
  
  # Tạo danh sách và đặt nó vào cửa sổ
  treeview = ttk.Treeview(root, columns=("Column 1", "Column 2"), show="headings")
  treeview_x = ttk.Treeview(root, columns=("Column 1", "Column 2", 'Column 3', 'Column 4', 'Column 5'), show="headings")
  treeview.grid(row=0, column= 0, padx= 0, pady= 0)
  
  # Đặt tên cho các cột
  treeview.heading("Column 1", text="lname%fname")
  treeview.heading("Column 2", text="File ID")
  # Cấu hình căn giữa cho mỗi cột
  treeview.column("Column 1", anchor="center")
  treeview.column("Column 2", anchor="center")

  for file in file_list:
    treeview.insert("", "end", values=(file['file_name'], file['file_md5']))

  root.after(100, lambda: check(treeview=treeview, conn=conn, session_id=session_id))

  # Tạo nút để chọn tệp và thêm vào danh sách
  add_file_button = tk.Button(root, text="Add File", command=add_file_to_list)
  add_file_button.grid(row=1, column=0, padx=10, pady=10)

  frame = tk.Frame(root)
  frame.grid(row=2, column=0, padx=10, pady=10)

  seek_file = tk.Label(frame, text="Nhập file:")
  seek_file.grid(row=1, column=0, padx=10, pady=10)
  
  seek_file_entry = tk.Entry(frame)
  seek_file_entry.grid(row=2, column=0, padx=10, pady=10)

  # Client nhap ten file can tim kiem
  submit_button = tk.Button(frame, text="Submit", command=lambda: find_source_files(treeview=treeview_x,
    message=f'FIND_{seek_file_entry.get()}_{session_id}'.encode('utf-8')
  ))
  submit_button.grid(row=2, column=1)
  treeview_x.bind('<<TreeviewSelect>>', download_from_source)

  # Client dang xuat he thong
  exit_button = tk.Button(root, text='Log out', command= lambda: sys.exit(0))
  exit_button.grid(row=5,column=0,padx=10, pady=10)
  
  # Bắt đầu vòng lặp chính của ứng dụng
  root.mainloop()


# abcxyz
def user_cli(session_id:str):
  HOST = '10.0.130.251'
  PORT_SERVER = 3000
  session = session_id 
  while True:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    my_socket.connect((HOST, PORT_SERVER))
    userInput = input(f"Session {session} : ")
    my_socket.send(f"{userInput}_{session}".encode('utf-8'))
    rcv_message = f'{my_socket.recv(2000).decode("utf-8")}'
    shell.print_red(rcv_message)
    if rcv_message[:4] == "ALGI":
      session = rcv_message[4:]
    elif rcv_message[:4] == "ADRE":
      client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
      HOST_download = input("Input source node ip you want to download : ")
      PORT_download = int(input("Input source node port you want to download : "))
      client_socket.connect((HOST_download, PORT_download))
      client_socket.send(f"Please send me {rcv_message.split(' ')[-1]}".encode('utf-8')) 
      file_name = client_socket.recv(1024).decode('utf-8')
      print("\n")
      print(f"File name: {file_name}")
      file_size = client_socket.recv(1024).decode('utf-8')
      print(f"File size: {file_size}")

      file = open(file_name, "wb")
      file_bytes = b""
      done = False
      pbar  = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(file_size))
      while not done:
        data = client_socket.recv(1024)
        if file_bytes[-5:] == b"<END>":
          done = True
        else:
          file_bytes += data
        pbar.update(1024)
      pbar.close()
      file.write(file_bytes)
      file.close()
      client_socket.close()
    my_socket.close()


# Client yeu cau file gui request duoc ket noi va duoc Share file do:
def show_dialog(message:str, client_address:str):
    app = QApplication(sys.argv)
    message = f"Message from {client_address} : {message}. Đồng ý kết nối và gửi file?"
    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Question)
    dialog.setText(message)
    dialog.setWindowTitle("Question")
    dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    result = dialog.exec()
    if result == QMessageBox.Yes:
        return True 
    elif result == QMessageBox.No:
        return False
    else:
        print("Dialog closed or an error occurred")


def source_node(session_id:str):
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  PORT = peer_repository.find(conn=conn, session_id=session_id).port
  HOST = peer_repository.find(conn=conn, session_id=session_id).ip
  conn.close()
  # HOST = socket.gethostbyname(socket.gethostname())
  def child(client_socket, file_path):
    file = open(file_path, 'rb')
    file_size = os.path.getsize(file_path)
    file_name = file_path.split('/')[-1]
    client_socket.send(file_name.encode())
    client_socket.send(str(file_size).encode())

    data = file.read()
    client_socket.sendall(data)
    client_socket.send(b"<END>")
    file.close()
    client_socket.close()


  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((HOST, int(PORT)))
  server.listen()

  while True:
    client_socket, client_address = server.accept()
    print(f"Connection from {client_address}")
    request = client_socket.recv(1024).decode('utf-8')
    result = messagebox.askyesno("Flash Message", "Đồng ý gửi file?")
    if(result):
      file = filedialog.askopenfilename()
      if(file):
        t = threading.Thread(target=child, args=(client_socket, file,))
        t.daemon = True
        t.start()
      else:
        client_socket.close()
    else:
      client_socket.close()
    

def logic(root, username:str, password:str):
  try:
    conn = database.get_connection(db_file)
    conn.row_factory = database.sqlite3.Row
  except database.Error as e:
    print(f'Error: {e}')
  peer_account = peer_repository.find_account(conn=conn, username=username)
  if peer_account is not None:
    if password == peer_account.password_account:
      peer = peer_repository.find(conn, peer_account.session_id)
      # peer.ip = socket.gethostbyname(socket.gethostname())
      peer.ip = peer_repository.find(conn=conn, session_id=peer_account.session_id).ip
      peer.state_on_off = True
      peer.update(conn)
      conn.commit()

      root.destroy()
      thread2 = threading.Thread(target=main_view, args=(peer_account.session_id,))
      thread1 = threading.Thread(target=user_cli, args=(peer_account.session_id,))
      thread3 = threading.Thread(target=source_node, args=(peer_account.session_id,))
   
      thread1.daemon = True
      thread3.daemon = True
      
      thread2.start() 
      thread1.start()
      thread3.start()   
      thread2.join()
      peer.state_on_off = False
      peer.update(conn)
      conn.commit()
      conn.close()  
    else:
      messagebox.showerror("Lỗi", "Mật khẩu không đúng !")
  else:
    messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không đúng !")
       
   
def login():
  root = tk.Tk()
  root.title("Đăng nhập")
  username_label = tk.Label(root, text="Tên tài khoản:")
  username_label.pack()
  username_entry = tk.Entry(root)
  username_entry.pack()

  password_label = tk.Label(root, text="Mật khẩu:")
  password_label.pack()
  password_entry = tk.Entry(root, show="*")  # Đặt show="*" để ẩn mật khẩu
  password_entry.pack()
  # Tạo và đặt nút Đăng ký
  register_button = tk.Button(root, text="Login", command=lambda: logic(root, username=username_entry.get(),password=password_entry.get()))
  register_button.pack()
  # Tạo và đặt nút Đăng ký
  register_button = tk.Button(root, text="Sign up", command=lambda: register(root=root))
  register_button.pack()
  root.mainloop()

login()
   