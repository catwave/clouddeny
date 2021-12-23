# clouddeny
generate .htaccess to deny various cloud providers

pip install -r requirements.txt

python gen.py --aws --az --gcp --oci --do | tee .htaccess
