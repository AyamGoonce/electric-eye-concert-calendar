(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e996ccdadd7c1b13.js","sha256":"e996ccdadd7c1b139fc54daf9d5c3b291655300509fe1e639f81e003b9d02f46","count":244});
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
