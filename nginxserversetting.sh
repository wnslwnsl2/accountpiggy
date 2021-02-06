#!/bin/bash
{
#uwsgi.service 파일을 데몬에 등록하기
#sudo ln -f /srv/nbbanggogo/.config/uwsgi/uwsgi.service /etc/systemd/system/uwsgi.service;

#Django 내의 nginx 설정 파일을 nginx 어플리케이션에 등록해야 한다.
sudo cp -f /srv/accountpiggy/.config/nginx/accountpiggy.conf /etc/nginx/sites-available/accountpiggy.conf;
#sited-available에 복사된 설정 파일을 sites-enables폴더 안에서도 링크해준다.
sudo ln -sf /etc/nginx/sites-available/accountpiggy.conf /etc/nginx/sites-enabled/accountpiggy.conf;

sudo systemctl daemon-reload;
sudo systemctl restart uwsgi nginx;
}