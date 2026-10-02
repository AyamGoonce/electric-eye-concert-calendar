(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.cb2fbfb401302098.js","sha256":"cb2fbfb401302098a6ed3ca810ea876cf33718dbcbfb2747763ff28929533f39","count":247});
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
