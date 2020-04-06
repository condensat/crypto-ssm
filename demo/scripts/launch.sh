source /demo/scripts/set_aliases.sh

b-dae && sleep 2 && e1-dae && e2-dae && e3-dae

sleep 5

e1-cli generatetoaddress 1 $(e1-cli getnewaddress)

sleep 1

python3.6m /demo/master_blinding_key.py
