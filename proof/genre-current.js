(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.571be96f699c6e27.js","sha256":"571be96f699c6e276080af2916ca9ea0591ea2f6e1a1b0755daf3aa1c005b5dc","count":244});
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
