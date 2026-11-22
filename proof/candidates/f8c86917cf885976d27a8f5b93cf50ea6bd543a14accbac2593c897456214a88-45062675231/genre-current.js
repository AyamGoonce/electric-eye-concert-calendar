(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.51a8270c58fb87bb.js","sha256":"51a8270c58fb87bba723a6b0769a30c176b80e026787dd917e10a9b659877e4f","count":244});
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
