su jenkins
cd ~/.ssh
cat id_rsa.pub >> authorized_keys
rm -rf id_rsa.pub
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys