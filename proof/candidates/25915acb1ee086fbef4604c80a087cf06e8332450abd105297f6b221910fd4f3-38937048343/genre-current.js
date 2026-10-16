(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.366a3b05ba647e01.js","sha256":"366a3b05ba647e01f103509ef32ff72b6d7178e9a82d052f80742c98b83d6ff2","count":244});
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
