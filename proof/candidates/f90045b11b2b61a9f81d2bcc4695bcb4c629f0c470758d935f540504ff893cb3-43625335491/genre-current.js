(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c5cb45c622d3a6e1.js","sha256":"c5cb45c622d3a6e18b02a437eb90b01e212e2530a6f0b1dc27ee006481ba362a","count":244});
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
