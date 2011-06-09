%define name sipfwd
%define version 0.7.2
%define release %mkrel 1

Summary: Stateless SIP Proxy
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}_%{version}.tar.gz
Source1: %{name}.sysinit
License: GPLv2+
Group: System/Servers
Url: http://dev.cmeerw.org/node/172
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: libosip2-devel
BuildRequires: udns-devel
BuildRequires: sqlite3-devel
BuildRequires: sqlite3-tools

%description
SIPFwd is a SIP forwarding daemon that acts as a stateless SIP proxy to
essentially forward a SIP address to another SIP server. This is useful
if you already have an account with a SIP provider, but aren't too happy
about the SIP URL you got and instead prefer to use a SIP URL with your
own domain name (but don't want to run a full-blown SIP server like
Asterisk or OpenSER).

So it allows you to use and publish SIP URLs of the form
sip:user@example.com with the minimum possible effort.

Of course, your existing SIP provider has to allow incoming connections
via SIP (unfortunately, some providers choose to block direct SIP connections
and only allow connections via PSTN).


%prep
%setup -q

%apply_patches

%build
#configure2_5x

%make

%install
rm -rf %{buildroot}
%makeinstall_std
install -D -m 0755 %{_sourcedir}/%{name}.sysinit %{buildroot}%{_sysconfdir}/init.d/%{name}
install -d %{buildroot}%{_localstatedir}/run/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}
sqlite3 %{buildroot}%{_localstatedir}/lib/%{name}/db.empty.sqlite <db.sqlite

%post
%_post_service %{name}

# Add sip entries in /etc/services (needed for name resolution)
if ! grep -qE '^sip[[:space:]]+5060/udp' %{_sysconfdir}/services; then
        # cleanup
        echo "# SIP ports added by %{name}" >> /etc/services
        echo -e "sip\t5060/udp\t\t\t\t# Session Initiation Protocol (VoIP)" >> /etc/services
fi

# Do not clobber the users own database on updates etc.
if [ ! -f %{_localstatedir}/lib/%{name}/db.sqlite ]; then
	cp -a %{_localstatedir}/lib/%{name}/db.empty.sqlite %{_localstatedir}/lib/%{name}/db.sqlite
fi


%preun
%_preun_service %{name}

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/false

%postun
%_postun_userdel %{name}

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root)
%doc README
%{_sbindir}/%{name}
%{_sysconfdir}/init.d/%{name}
%attr(755,%{name},%{name}) %dir %{_localstatedir}/lib/%{name}
%attr(755,%{name},%{name}) %{_localstatedir}/lib/%{name}/db.empty.sqlite
%attr(755,%{name},%{name}) %dir %{_localstatedir}/run/%{name}
%{_docdir}/%{name}/db.sqlite
