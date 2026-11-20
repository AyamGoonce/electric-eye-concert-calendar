(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ad7207c78b62b991.js","sha256":"ad7207c78b62b991ca629b034bcfb99dca5a640b3f450c21da9ebed2ce6bb606","count":244});
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
