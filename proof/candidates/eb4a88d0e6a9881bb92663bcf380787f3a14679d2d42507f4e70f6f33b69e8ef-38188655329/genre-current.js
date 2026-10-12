(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.85456cc09e35e229.js","sha256":"85456cc09e35e229b6c317738bf50e2b7c0166af9e22f1d95b7f98cdb1da5354","count":244});
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
