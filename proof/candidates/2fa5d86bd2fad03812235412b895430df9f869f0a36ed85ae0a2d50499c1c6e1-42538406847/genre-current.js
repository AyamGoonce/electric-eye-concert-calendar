(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5d3a0158a4b5d260.js","sha256":"5d3a0158a4b5d2600b778195c38169e2c48525870df326054a87cda0c81f23d7","count":244});
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
