{
  inputs = {
    src-artiq_tektronix_osc = { url = github:elhep/artiq_tektronix_oscilloscope; flake = false; };
    artiq.url = "git+https://github.com/m-labs/artiq.git?ref=release-7&rev=38c72fdab41679c300c235d960e87b9e06bea5b4";
    artiq-comtools.follows = "artiq/artiq-comtools";
    artiq-extrapkg = {
      url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git?ref=release-7";
      inputs.artiq.follows = "artiq";
    };
    nixpkgs.follows = "artiq/nixpkgs";
    
  };

  outputs = { self, artiq, artiq-comtools, artiq-extrapkg, nixpkgs, src-artiq_tektronix_osc }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };
      # Combine attribute sets for convenience
      artiq-full = artiq.packages.x86_64-linux // artiq-comtools.packages.x86_64-linux // artiq-extrapkg.packages.x86_64-linux;

      artiq_tektronix_osc = pkgs.python3Packages.buildPythonPackage rec {
        pname = "artiq_tektronix_osc";
        version = "1.0.0";
        src = src-artiq_tektronix_osc;
        propagatedBuildInputs =  [artiq.inputs.sipyco.packages.x86_64-linux.sipyco] ++
          (with pkgs.python3Packages; [ pyvisa-py zeroconf psutil numpy ]);
        patches = [ ./tektronix.patch ]; # setup.py tries to pull sipyco from git, fails
      };

    in
    {
      # Default shell for `nix develop`
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = [
          # Python packages
          (pkgs.python3.withPackages (ps: [
            # From the artiq flake
            artiq-full.artiq

            # From artiq-extrapkg
            artiq-full.dax
            # artiq-full.dax-applets
            # artiq-full.flake8-artiq

            # Additional packages
            artiq-full.artiq-comtools
            # ps.paramiko # needed for flashing boards remotely (artiq_flash -H)
            artiq_tektronix_osc
          ]))
          # Non-Python packages
          # artiq-full.openocd-bscanspi # needed for flashing boards, also provides proxy bitstreams
        ];
      };
      # Enables use of `nix fmt`
      formatter.x86_64-linux = pkgs.nixpkgs-fmt;
    };

  # Settings to enable substitution from the M-Labs servers (avoiding local builds)
  nixConfig = {
    extra-trusted-public-keys = [
      "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc="
    ];
    extra-substituters = [ "https://nixbld.m-labs.hk" ];
  };
}
