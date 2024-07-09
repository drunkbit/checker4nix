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
    # note: add python packages into requirements.txt file
    # note: if vscode does not detect python module from requirements.txt, change python interpreter (bottom right corner)
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
      # allow use of wheels
      SOURCE_DATE_EPOCH=$(date +%s)

      # setup virtual environment if it does not already exist
      VENV=.venv
      if test ! -d $VENV; then
        virtualenv $VENV
      fi
      source ./$VENV/bin/activate
      export PYTHONPATH=`pwd`/$VENV/${myPython.sitePackages}/:$PYTHONPATH

      # install packages from requirements.txt via pip
      pip install --disable-pip-version-check -r requirements.txt
    '';
  };
in

shell
