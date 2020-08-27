'''
CONFDIR=/etc/bitcoin/
DATADIR=/var/lib/bitcoind/
LOGDIR=/var/log/bitcoind/

BIN=/usr/local/bin/bitcoind

# First check if bitcoind is installed on the system with root

if [ ! -f "$BIN" ]; then
'''
# only if bitcoind bin does not exist

	# install dependencies

	apt-get update -yy && apt-get upgrade -yy && \
	apt-get install git build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 -yy  && \
	apt-get install libssl-dev libevent-dev libboost-system-dev libboost-filesystem-dev libboost-test-dev libboost-thread-dev -yy

	# if no bitcoin repo, clone bitcoin core repo and checkout the last label
	if [ ! -d "bitcoin" ]; then
		git clone https://github.com/bitcoin/bitcoin.git
	fi
	cd bitcoin
	TAG=$(git describe --tags $(git rev-list --tags --max-count=1))
	git checkout tags/$TAG -b last_release

	# configure and compile

	./contrib/install_db4.sh `pwd`
	export BDB_PREFIX="$PWD/db4"
	./autogen.sh
	./configure BDB_LIBS="-L${BDB_PREFIX}/lib -ldb_cxx-4.8" BDB_CFLAGS="-I${BDB_PREFIX}/include" --with-gui=no --without-miniupnpc
	make -j$(nproc) && sudo make install
	cd ..
'''
fi

if [ ! -f "/lib/systemd/system/bitcoind.service" ]; then
	wget https://raw.githubusercontent.com/Sosthene00/bitcoin/init_files/contrib/init/bitcoind.service
	mv bitcoind.service /lib/systemd/system/bitcoind.service
fi

# create bitcoin user if needed

user_exists=$(id -u bitcoin > /dev/null 2>&1; echo $?)
if [ user_exists == 1 ]; then
	echo "Please create user bitcoin and run this script again"
	exit
fi

# create and configure the dir if necessary

if [ ! -f "$CONFDIR" ]; then
	mkdir $CONFDIR && \
	cp /home/sosthene/bitcoin.conf $CONFDIR && \
	chown -R bitcoin:bitcoin $CONFDIR
fi

if [ ! -f "$DATADIR" ]; then
	mkdir $DATADIR && \
	chown -R bitcoin:bitcoin $DATADIR
fi

if [ ! -f "$LOGDIR" ]; then
	mkdir $LOGDIR && \
	chown -R bitcoin:bitcoin $LOGDIR
fi
'''