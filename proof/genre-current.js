(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1278baa1d1f328a1.js","sha256":"1278baa1d1f328a18c506b4de8c08d998d6421d39f36e5ff1e45facc56b9ad64","count":244});
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
