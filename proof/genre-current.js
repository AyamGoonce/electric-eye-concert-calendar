(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ec610b4a2710bcfa.js","sha256":"ec610b4a2710bcfa87557545964e3131c082366cd1ddfdf4e1a06bb386be17fb","count":244});
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
