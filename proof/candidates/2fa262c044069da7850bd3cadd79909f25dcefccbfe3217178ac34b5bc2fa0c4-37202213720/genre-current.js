(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.23ad8dec67af9992.js","sha256":"23ad8dec67af99926fe1fde6c178f9f9f7637cd5be95b1ed2669b474a4ee768d","count":244});
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
