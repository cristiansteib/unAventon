# Project "Un Aventon"
Server: [https://unaventon.debuguear.com/](https://unaventon.debuguear.com/) , is synchronized in real time over the branch stable


How to install your own instance server
---------------------------------------
Clone the repository
```bash
git clone git://github.com/arNTC/unAventon.git
```

Install the requirements for python3
```bash
pip3 install -r requirements.txt
```

Build the databases
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```
Run the server
```
python3 manage.py runserver 0.0.0.0:8000
```

Configure the email sender
```
echo "yourmail@gmail.com" > '~/.gmail-user'
echo "yourPassword" > '~/.gmail-password'
```

Now go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Contributing

#### Credits
* Muiña, Sebastian Gabriel
* Steib, Cristian
