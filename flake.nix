{
  inputs = {
    src-artiq_tektronix_osc = { url = git+https://github.com/elhep/artiq_tektronix_oscilloscope.git?ref=dev/dax_sim; flake = false; };
    artiq.url = "git+https://github.com/m-labs/artiq.git?ref=release-7&rev=38c72fdab41679c300c235d960e87b9e06bea5b4";
    artiq-comtools.follows = "artiq/artiq-comtools";
    artiq-extrapkg = {
      url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git?ref=release-7";
      inputs.artiq.follows = "artiq";
    };
    nixpkgs.follows = "artiq/nixpkgs";

    dax = {
      url = git+https://gitlab.com/duke-artiq/dax.git;
      inputs = {
        artiqpkgs.follows = "artiq";
        nixpkgs.follows = "artiq/nixpkgs";
        sipyco.follows = "artiq/sipyco";
      };
    };
    dax-applets = {
      url = git+https://gitlab.com/duke-artiq/dax-applets.git;
      inputs = {
        artiqpkgs.follows = "artiq";
        nixpkgs.follows = "artiq/nixpkgs";
      };
    };
  };

  outputs = { self, artiq, artiq-comtools, artiq-extrapkg, nixpkgs, src-artiq_tektronix_osc, dax, dax-applets }:
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

      dax_pkg = dax.packages.x86_64-linux;
      dax-applets_pkg = dax-applets.packages.x86_64-linux;

    in rec
    {
      # Default shell for `nix develop`
      devShells.x86_64-linux.default = pkgs.mkShell {
        buildInputs = [
          # Python packages
          (pkgs.python3.withPackages (ps: [
            # From the artiq flake
            artiq-full.artiq
            artiq-full.misoc
            ps.imageio
            # I need to build dax from source because artiq-extrapkg is pointing to dax release 6.7
            dax_pkg.dax
            dax-applets_pkg.dax-applets
            # From artiq-extrapkg
            # artiq-full.dax
            # artiq-full.dax-applets
            # artiq-full.flake8-artiq

            # Additional packages
            artiq-full.artiq-comtools
            # ps.paramiko # needed for flashing boards remotely (artiq_flash -H)
            artiq_tektronix_osc

            # Packages for testing
            ps.pytest
            ps.coverage
          ]))
          # Non-Python packages
          artiq-full.openocd-bscanspi # needed for flashing boards, also provides proxy bitstreams
        ];
      };
      # Enables use of `nix fmt`
      formatter.x86_64-linux = pkgs.nixpkgs-fmt;
      packages.x86_64-linux.default = pkgs.buildEnv{
		name="qce24-artiq-tutorial";
		paths = devShells.x86_64-linux.default.buildInputs;
	};
    };

  # Settings to enable substitution from the M-Labs servers (avoiding local builds)
  nixConfig = {
    extra-trusted-public-keys = [
      "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc="
    ];
    extra-substituters = [ "https://nixbld.m-labs.hk" ];
  };
}
