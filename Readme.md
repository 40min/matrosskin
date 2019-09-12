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
        * add classifier
        * filter output
        * scheduled re-education of classifier based on ratings
        * backup ratings to dropbox
    * Add merge news tool

* Mushrooms
    * Receive/save picture
    * install mushrooms lib
    
* Weather
    * Better approve button
        
* Talks
    * Weather integration (use action instead of text)

* Common-tech:
    * better message routing
    * handle errors
    * create help-page with commands-list
    * add suspend/resume commands
    * raise broadcast messages for subscribers
    * refactor config.yaml
    * refactor data and dropbox sync to store data files in folders
    * Update telegram-bot lib: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-12.0
    * Remove dependency from certain files: rated_news.csv, rated_bash
    * Update dialogflow lib: https://cloud.google.com/dialogflow/docs/reference/libraries/python
    
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
# create config.yml


```
    