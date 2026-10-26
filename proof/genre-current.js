(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c289bf0d3bcd0653.js","sha256":"c289bf0d3bcd0653a282bb916ca56da01d437831e242c190cd0d2da164d5f6ba","count":244});
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
