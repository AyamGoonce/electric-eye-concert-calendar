(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.d4d1d000f5f8151f.js","sha256":"d4d1d000f5f8151fd18f833886d45b0efca5928f09e00b7ea113129c22f84068","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
