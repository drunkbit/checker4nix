# Welcome to checker4nix 👋

Just a little tool to check if nix packages are up to date (compared to flathub as source)

## Run

To use checker4nix, follow these steps:

``` python
git clone https://github.com/drunkbit/checker4nix
cd checker4nix
python src/checker4nix.py
```

> [!NOTE]
> There is a nix-shell available: `nix-shell`

## Output

The output contains the following information:

* missing: could not find a nix package for flathub package
* false: flathub and nix packages have different versions
* true: flathub and nix packages have the same version

## TODOs

- [ ] Delete old files based on time
- [ ] Compare packages faster and more efficient
- [ ] Prevent duplicates in comparison
