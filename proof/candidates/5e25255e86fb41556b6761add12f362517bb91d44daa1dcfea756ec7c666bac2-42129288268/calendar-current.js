(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5e25255e86fb4155.js","sha256":"5e25255e86fb41556b6761add12f362517bb91d44daa1dcfea756ec7c666bac2","count":2046,"publishedAt":"2026-11-05T23:28:56Z","state":"calendar-state.json","stateSha256":"d74ca548c2c06eb8696e7e97e462196ea5c07d3430f2786e092f845d2af9e291","sourceState":"calendar-source-state.json","sourceStateSha256":"fc16d595674024b41ea53bf104d51d9b92d71218c2f80761d62f509cb60b0be0"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
