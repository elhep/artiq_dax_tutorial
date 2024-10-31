{
  inputs = {
    src-artiq_tektronix_osc = { url = git+https://github.com/elhep/artiq_tektronix_oscilloscope.git; flake = false; };
    artiq.url = "git+https://github.com/m-labs/artiq.git?ref=release-8&rev=431c415423e709178263d3463f8c4ab905e9b796";
    artiq-comtools.follows = "artiq/artiq-comtools";
    artiq-extrapkg = {
      url = "git+https://git.m-labs.hk/M-Labs/artiq-extrapkg.git?ref=release-8";
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
        buildInputs = [artiq.inputs.sipyco.packages.x86_64-linux.sipyco];
        propagatedBuildInputs = (with pkgs.python3Packages; [ pyvisa-py zeroconf psutil numpy ]);
        patches = [ ./tektronix.patch ]; # setup.py tries to pull sipyco from git, fails
      };

      makeArtiqBoardPackage = variant: artiq.makeArtiqBoardPackage {
        target = "kasli";
        variant = variant;
        buildCommand = 
          "python -m artiq.gateware.targets.kasli ${./firmware}/${variant}.json";
      };

      makeVariantDDB = variant: pkgs.runCommand "ddb-${variant}"  
      {
        buildInputs = [
          artiq.devShells.x86_64-linux.boards.buildInputs
        ];
      }
      ''
      mkdir -p $out
      artiq_ddb_template ${./firmware}/${variant}.json -o $out/device_db.py
      '';

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
            ps.pillow

            # Additional packages
            # ps.paramiko # needed for flashing boards remotely (artiq_flash -H)
            artiq_tektronix_osc
          ]))
          # Non-Python packages
          artiq-full.openocd-bscanspi # needed for flashing boards, also provides proxy bitstreams
        ];
      };
      packages.x86_64-linux.default = pkgs.buildEnv{
        name="qce24-artiq-tutorial";
        paths = devShells.x86_64-linux.default.buildInputs;
      };
      packages.x86_64-linux = {
        tutorial = makeArtiqBoardPackage "tutorial";

        ddb_tutorial = makeVariantDDB "tutorial";
      };
    };

  # Settings to enable substitution from the M-Labs servers (avoiding local builds)
  nixConfig = {
    extra-trusted-public-keys = [
      "nixbld.m-labs.hk-1:5aSRVA5b320xbNvu30tqxVPXpld73bhtOeH6uAjRyHc="
    ];
    extra-substituters = [ "https://nixbld.m-labs.hk" ];
    extra-sandbox-paths = "/opt";
  };
}
