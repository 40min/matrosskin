# Todo
    
* News
    * Generate news 
        - from time-to time 
        - mixed with chat-model
        - triggered by words
    * Add education of new model based on chat
    * Add filter fun/not-fun
        * backup ratings to dropbox

* Mushrooms
    * Receive/save picture
    * install mushrooms lib
    
* Talks
    * Weather integration (use action instead of text)

* Common-tech:
    * better message routing
    * handle errors
    * raise broadcast messages for subscribers
    
# AWS prepare
```bash
sudo yum update -y
sudo yum install -y docker git

sudo service docker start
sudo usermod -a -G docker ec2-user
# relogin after
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose


git clone https://github.com/40min/matrosskin.git
cd matrosskin
git checkout dev

cp .env.example .env
# edit .env
# copy you google cloud key into the file gcp_key.json into the root of the project

```
    