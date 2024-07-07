# source: https://gist.github.com/cdepillabout/f7dbe65b73e1b5e70b7baa473dafddb3

let
  # use unstable branch for latest versions
  nixpkgs-src = builtins.fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-unstable";

  # allow unfree packages or not
  pkgs = import nixpkgs-src { config = { allowUnfree = false; }; };

  # python version
  myPython = pkgs.python3;

  # python packages
  pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
    black
    ipython
    pip
    setuptools
    virtualenvwrapper
    wheel
  ]);

  shell = pkgs.mkShell {
    buildInputs = with pkgs; [
      # python version with python packages from above
      pythonWithPkgs

      # formatter for this file
      nixpkgs-fmt
    ];

    shellHook = ''
      # allow the use of wheels
      SOURCE_DATE_EPOCH=$(date +%s)

      # setup the virtual environment if it does not already exist
      VENV=.venv
      if test ! -d $VENV; then
        virtualenv $VENV
      fi
      source ./$VENV/bin/activate
      export PYTHONPATH=`pwd`/$VENV/${myPython.sitePackages}/:$PYTHONPATH
    '';
  };
in

shell
