(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.80a5e795781cc8f7.js","sha256":"80a5e795781cc8f7c99d35703000e1a5d2a38f10ad3e4f4c3e29ff715fb2317f","count":244});
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
