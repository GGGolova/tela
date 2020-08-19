# Project: Tela

RESTful web application using the Python framework Flask along with implementing third-party OAuth authentication.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Installation](#installation)
- [Run Web Application](#run-web-application)

---

## Installation

#### 1.  Install Git, VirtualBox and Vagrant.

Download and Install Git : 
http://git-scm.com/downloads

Download and Install Virtual Box : 
https://www.virtualbox.org/wiki/Download_Old_Builds_5_2

Download and Install Vagrant : 
https://www.vagrantup.com/downloads.html


#### 2. In Git Bash terminal, clone [Tela Project.](https://github.com/igorzanine/tela.git)
```
git clone https://github.com/igorzanine/tela.git tela
```

#### 3. Change to `tela/vagrant` directory and launch virtual machine.
```
cd tela/vagrant
vagrant up
```

#### 4. Log into virtual machine.
```
vagrant ssh
```

---

## Run _Item Catalog_ Web Application

#### 1. Initiate Web Application within virtual machine.

With python 2:
```
python /vagrant/catalog/application.py
```

Or with python 3:
```
python3 /vagrant/catalog/application.py
```

#### 2. In your preferred web browser address line navigate to local host port 8080.
- [http://localhost:8080](http://localhost:8080)

At this point you should see your browser display _Item Catalog_ web application. You may login with Google. Once logged in, you may create, update and delete items (CRUD).


JSON objects could be accessed at:
- [http://localhost:8080/Category/JSON](http://localhost:8080/Category/JSON)
- [http://localhost:8080/Item/JSON](http://localhost:8080/Item/JSON)


#### 3. Google API.

To be able to login with Google, you will need to update _client ID_ and _Client secret_ fields in  _client_secret.json_ file.