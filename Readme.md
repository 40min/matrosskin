# Todo
    
* News
    * Generate news 
        - from time-to time 
        - mixed with chat-model
        - triggered by words
    * Rate generated news
        * rate as polling
    * Add education of new model based on chat
    * Add news squash-by-days utility
    * Add filter fun/not-fun
        * backup ratings to dropbox
    * Add merge news tool

* Mushrooms
    * Receive/save picture
    * install mushrooms lib
    
* Talks
    * Weather integration (use action instead of text)
    
* FriendsFinder
    * One user search another with nickname
    * Bot should save user's nickname->chat_id mapping
    * If user search another and chat_id is present then show
    searchable user request to share coordinates with req_time/nickname 
    from another user
    * open google-maps on phone with coordinates: see here https://developers.google.com/maps/documentation/urls/android-intents

* Common-tech:
    * better message routing
    * handle errors
    * add suspend/resume commands
    * raise broadcast messages for subscribers
    * refactor data and dropbox sync to store data files in folders
    * Remove dependency from certain files: rated_news.csv, rated_bash
    
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
    