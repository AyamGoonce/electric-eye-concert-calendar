(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7a1454102543cdcf.js","sha256":"7a1454102543cdcf1520e28379319e77fa3a7f889a38bb1f61e8f2b49ced5ab9","count":245});
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
