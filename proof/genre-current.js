(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.62f9f0f44bc887b5.js","sha256":"62f9f0f44bc887b5eecd8d9eef37c60528f8eb6266c98857be9fe32ef5deba51","count":244});
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
