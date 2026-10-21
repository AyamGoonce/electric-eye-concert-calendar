(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b64506b6ded24dd5.js","sha256":"b64506b6ded24dd58c24b7d177f89d6a70e7a8664e706d5d896afccbe01d2a00","count":244});
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
