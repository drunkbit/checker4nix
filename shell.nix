# source: https://gist.github.com/cdepillabout/f7dbe65b73e1b5e70b7baa473dafddb3

let
  # use unstable branch for latest versions
  nixpkgs-src = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-unstable";

  # allow unfree packages or not
  pkgs = import nixpkgs-src { config = { allowUnfree = true; }; };

  # python version
  myPython = pkgs.python3;

  # python packages
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    # note: add python packages into requirements.txt file instead of here
    black
    ipython
    pip
    setuptools
    virtualenvwrapper
    wheel
  ]);

  lib-path = with pkgs; lib.makeLibraryPath [
    libffi
    openssl
    stdenv.cc.cc
  ];

  shell = pkgs.mkShell {
    buildInputs = with pkgs; [
      # python version with python packages from above
      pythonWithPkgs

      # other packages needed for compiling python libs
      libffi
      openssl
      readline

      # unfortunately needed because of messing with LD_LIBRARY_PATH below
      git
      openssh
      rsync

      # formatter for this file
      nixpkgs-fmt

      # need to run this project
    ];

    shellHook = ''
      # allow use of wheels
      SOURCE_DATE_EPOCH=$(date +%s)

      # augment dynamic linker path
      export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"

      # setup virtual environment if it does not already exist
      VENV=$HOME/.venv
      if test ! -d $VENV; then
        virtualenv $VENV
      fi
      source $VENV/bin/activate
      export PYTHONPATH=$VENV/${myPython.sitePackages}/:$PYTHONPATH

      # install packages from requirements.txt via pip
      pip install --disable-pip-version-check -r requirements.txt
    '';
  };
in

shell
