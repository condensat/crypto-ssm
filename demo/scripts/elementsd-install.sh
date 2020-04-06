'''
CONFDIR=/etc/elements/
DATADIR=/var/lib/elementsd/
LOGDIR=/var/log/elementsd/
BIN=/usr/local/bin/elementsd

# First check if elementsd is installed on the system with root

if [ ! -f "$BIN" ]; then
'''
# only if elementsd bin does not exist

	# install dependencies
	apt-get update -yy && apt-get upgrade -yy && \
	apt-get install git build-essential libtool autotools-dev automake pkg-config bsdmainutils python3 -yy  && \
	sudo apt-get install libssl-dev libevent-dev libboost-system-dev libboost-filesystem-dev libboost-test-dev libboost-thread-dev -yy

	# clone bitcoin core repo and checkout the last label

	if [ ! -d "elements" ]; then
		git clone https://github.com/ElementsProject/elements.git 
	fi
	cd elements
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

if [ ! -f "/lib/systemd/system/elementsd.service" ]; then
	wget https://raw.githubusercontent.com/Sosthene00/elements/init_files/contrib/init/elementsd.service
	mv elementsd.service /lib/systemd/system/elementsd.service
fi

# create bitcoin user if needed

user_exists=$(id -u elements > /dev/null 2>&1; echo $?)
if [ user_exists == 1 ]; then
	echo "Please create user elements and run this script again"
	exit
fi

# create and configure the dir if necessary

if [ ! -f "$CONFDIR" ]; then
	mkdir $CONFDIR && \
	cp /home/sosthene/elements.conf $CONFDIR && \
	chown -R elements:elements $CONFDIR
fi

if [ ! -f "$DATADIR" ]; then
	mkdir $DATADIR && \
	chown -R elements:elements $DATADIR
fi

if [ ! -f "$LOGDIR" ]; then
	mkdir $LOGDIR && \
	chown -R elements:elements $LOGDIR
fi
'''