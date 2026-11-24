(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b56c0fd8ef659d62.js","sha256":"b56c0fd8ef659d62a2c1c0fff996f2da213dd14e7330882832314103bf9631e7","count":244});
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
