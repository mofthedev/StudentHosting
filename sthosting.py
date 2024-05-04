# A CLI script to provide students with a simple hosting for educational purposes.
# @author Möf Selvi

import csv
import subprocess
import random
import string
import os
import pwd
import grp

def main():
    while True:
        print("\nOptions:")
        print("1. Enable userdir module for Apache")
        print("2. Install MariaDB")
        print("3. Process student information from students.csv")
        print("4. Create users.txt for newusers program (from student_infos.csv)")
        print("5. Run newusers program using users.txt")
        print("6. Create databases and database users for students")
        print("7. Reset system (delete databases, remove users)")
        print("8. Install PHP")
        print("9. Show databases and users")
        print("0. Exit")

        choice = input("Enter your choice (0-7): ")

        if choice == '1':
            enable_userdir_module()
        elif choice == '2':
            install_mariadb()
        elif choice == '3':
            process_student_info()
        elif choice == '4':
            create_users_file()
        elif choice == '5':
            run_newusers()
        elif choice == '6':
            create_databases_and_users()
        elif choice == '7':
            reset_system()
        elif choice == '8':
            install_php()
        elif choice == '9':
            show_db()
        elif choice == '0' or choice == 'exit':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def enable_userdir_module():
    try:
        subprocess.run(['a2enmod', 'userdir'], check=True)
        subprocess.run(['systemctl', 'restart', 'apache2'], check=True)
        print("userdir module enabled for Apache successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to enable userdir module.")

def install_mariadb():
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', 'mariadb-server', '-y'], check=True)
        # subprocess.run(['sudo', 'systemctl', 'start', 'mariadb.service'], check=True)
        print("MariaDB installed successfully.")
        print("Run 'sudo systemctl start mariadb.service'")
        print("and")
        print("'sudo mysql_secure_installation'.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to install MariaDB.")


def install_php():
    try:
        subprocess.run(['sudo', 'apt', 'update'], check=True)
        subprocess.run(['sudo', 'apt', 'install', 'php', 'libapache2-mod-php', 'php-mysql', 'php-zip', 'php-gd', 'php-mbstring', 'php-curl', 'php-xml', 'php-bcmath','-y'], check=True)
        subprocess.run(['sudo', 'systemctl', 'restart', 'apache2.service'], check=True)
        print("PHP installed successfully.")
        print("Run 'sudo nano /etc/apache2/mods-enabled/php8.x.conf' and edit the conf file.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to install MariaDB.")


def show_db():
    try:
        subprocess.run(
            ['sudo', 'mysql', '-u', 'root', '-e', f"SHOW DATABASES;"],
            check=True
        )
        subprocess.run(
            ['sudo', 'mysql', '-u', 'root', '-e', f"SELECT user FROM mysql.user;"],
            check=True
        )
    except Exception as elnx:
        print(f"Warning: {elnx}")



def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits # + string.punctuation # let it be just letters and numbers
    return ''.join(random.choice(characters) for _ in range(length))

def process_student_info():
    input_file = "students.csv"
    output_file = "student_infos.csv"
    headers = ["Student Number", "Linux Username", "Database User", "Database Name", "Linux Password", "Database Password"]

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            writer.writerow(headers)

            for row in reader:
                if row:
                    student_number = row[0]
                    linux_username = "st" + student_number
                    db_user = "dbusr" + student_number
                    db_name = "dbstorage" + student_number
                    linux_password = generate_random_password()
                    db_password = generate_random_password()

                    writer.writerow([student_number, linux_username, db_user, db_name, linux_password, db_password])

        print(f"Student information generated and saved to '{output_file}' successfully.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_users_file():
    input_file = "student_infos.csv"
    output_file = "users.txt"

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            reader = csv.DictReader(infile)
            
            for row in reader:
                linux_username = row['Linux Username']
                linux_password = row['Linux Password']
                
                home_dir = f"/home/{linux_username}"
                
                # format (username:password:UID:GID:comment:home_dir:shell)
                user_entry = f"{linux_username}:{linux_password}:::{linux_username}:{home_dir}:/bin/bash\n"
                outfile.write(user_entry)

        print(f"User accounts created and saved to '{output_file}' for newusers program.")

    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# def run_newusers():
#     users_file = "users.txt"

#     try:
#         # Run newusers command using users.txt file
#         subprocess.run(['sudo', 'newusers', users_file], check=True)
#         print("User accounts created successfully using newusers program.")
#     except subprocess.CalledProcessError as e:
#         print(f"Error: {e}")
#         print("Failed to create user accounts using newusers program.")


def run_newusers():
    users_file = "users.txt"

    try:
        subprocess.run(['sudo', 'newusers', users_file], check=True)
        print("User accounts created successfully using newusers program.")

        with open(users_file, 'r') as file:
            for line in file:
                if line.strip():
                    username = line.split(':')[0]
                    home_dir = line.split(':')[5]

                    public_html_dir = os.path.join(home_dir, 'public_html')
                    os.makedirs(public_html_dir, exist_ok=True)
                    os.chmod(public_html_dir, 0o755)
                    os.chmod(home_dir, 0o755)
                    uid = pwd.getpwnam(username).pw_uid
                    gid = grp.getgrnam(username).gr_gid
                    os.chown(public_html_dir, uid, gid)
                    print(f"Created 'public_html' directory for user '{username}' and set permissions for '{uid}':'{gid}'.")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to create user accounts using newusers program.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_databases_and_users():
    input_file = "student_infos.csv"
    try:
        with open(input_file, 'r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                student_number = row['Student Number']
                db_user = row['Database User'] #"dbusr" + student_number
                db_name = row['Database Name'] #"dbstorage" + student_number
                db_password = row['Database Password']

                conn = subprocess.run(
                    ['mysql', '-u', 'root'],
                    input=f"CREATE DATABASE IF NOT EXISTS {db_name};\n",
                    text=True,
                    check=True,
                    capture_output=True
                )

                # DB User & Privileges
                subprocess.run(
                    ['mysql', '-u', 'root', '-e', f"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY '{db_password}';"],
                    check=True
                )
                subprocess.run(
                    ['mysql', '-u', 'root', '-e', f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost';"],
                    check=True
                )

        print("Databases and database users created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to create databases and database users.")

def reset_system():
    input_file = "student_infos.csv"
    try:
        with open(input_file, 'r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                linux_username = row['Linux Username']
                db_user = row['Database User']
                db_name = row['Database Name']

                subprocess.run(
                    ['sudo', 'mysql', '-u', 'root', '-e', f"DROP DATABASE IF EXISTS {db_name};"],
                    check=True
                )
                subprocess.run(
                    ['sudo', 'mysql', '-u', 'root', '-e', f"DROP USER IF EXISTS '{db_user}'@'localhost';"],
                    check=True
                )

                try:
                    subprocess.run(['sudo', 'userdel', '--force', '--remove', linux_username], check=True)
                except Exception as elnx:
                    print(f"Warning: {elnx}")

        print("System reset completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print("Failed to reset the system.")

if __name__ == "__main__":
    main()