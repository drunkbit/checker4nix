# checker4nix

Just a little tool to check if the nix packages are up to date (compared to flathub as source)

## Run

To use checker4nix, follow these steps:

1. Clone the repository:
    ```
    git clone https://github.com/drunkbit/checker4nix
    cd checker4nix
    ```
2. Run the Python script:
    ```
    python src/checker4nix.py
    ```

## Tips

There is a nix-shell available. To use it, simply run the following command in the project directory:

```
nix-shell
```

## TODOs

- [ ] Delete old files based on time

- [ ] Export results into file

- [ ] Compare packages faster and more efficient

- [ ] Color output
