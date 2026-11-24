(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.af449b5e8089f9f3.js","sha256":"af449b5e8089f9f36fc503662f9ad84fb967b34cb59da85804d0a0255eef4e93","count":244});
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
