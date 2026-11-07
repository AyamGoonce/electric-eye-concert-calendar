(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1d87bbcfc1988daa.js","sha256":"1d87bbcfc1988daa906c64b07ebdff70a90ccb20999b858f35cd9cee479f763b","count":244});
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
