(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ddadf2fa8ab3eb77.js","sha256":"ddadf2fa8ab3eb777be2c5ac413a5880dbb03565d126a99e4db3b4c2a47b172c","count":244});
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
