project('pardus-lightdm-greeter')

subdir('po')

# install sources
install_subdir('src', install_dir : '/usr/share/pardus/pardus-lightdm-greeter', strip_directory : true)
install_data('data/main.ui', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
install_data('data/servers.txt', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')

# glib schema
install_data('data/gsettings.xml', install_dir : '/usr/share/glib-2.0/schemas/', rename: 'tr.org.pardus.lightdm.greeter.gschema.xml')

# config files
install_data('data/lightdm.conf', install_dir : '/usr/share/lightdm/lightdm.conf.d/', rename: '99-pardus.conf')
install_data('data/config.ini', install_dir : '/etc/pardus/', rename: 'greeter.conf')

# xgreeters file
install_data('data/greeter.desktop', install_dir : '/usr/share/xgreeters/', rename: 'pardus.desktop')

# cli
install_data('pardus-lightdm-greeter.sh', install_dir : '/usr/libexec/', rename: 'pardus-lightdm-greeter', install_mode: 'rwxr-xr-x')
install_data('src/cli.py', install_dir : '/usr/bin/', rename: 'pardus-login', install_mode: 'rwxr-xr-x')

# icons
install_subdir('data/icon', install_dir : '/usr/share/icons/hicolor/scalable/status', strip_directory : true)

# css
install_data('data/main.css', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
install_data('data/colors.css', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
install_data('data/colors-dark.css', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')

# default backgrounds
install_data('data/bg-dark.png', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
install_data('data/bg-light.png', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
install_data('data/emblem-pardus.svg', install_dir : '/usr/pardus/pardus-lightdm-greeter/data/')
