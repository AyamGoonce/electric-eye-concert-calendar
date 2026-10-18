(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f3e46731ad3b8384.js","sha256":"f3e46731ad3b83848f798bd7a9cc5421058563d6c93e8cc12c2e6dcc681f7557","count":244});
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
