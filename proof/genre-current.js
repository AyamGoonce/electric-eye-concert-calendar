(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3a61cec504d0a175.js","sha256":"3a61cec504d0a175ad81155c4c57741d5e2c9950df03f21ccddc2750a6ff708a","count":244});
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
